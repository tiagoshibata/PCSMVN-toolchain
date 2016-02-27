#include <fcntl.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

/// Space for 64 data words and start address, size and checksum.
#define BLOCK_SIZE		(64 * 2 + 3 * 2)

typedef struct {
	uint16_t start;
	uint16_t size;
	uint16_t data[64];
	uint16_t checksum;
} block_t;

static ssize_t do_read_data(int fd, void *block) {
	ssize_t data_read = 0;

	while (data_read < BLOCK_SIZE) {
		ssize_t read_status = read(fd, ((uint8_t *)block) + data_read, BLOCK_SIZE - data_read);
		switch (read_status) {
		case -1:
			perror("read");
			return -1;

		case 0:
			return data_read;

		default:
			data_read += read_status;
		}
	}
	return data_read;
}

/**
 * Convert block data to native endianess.
 * @param[in,out] data Data to convert.
 * @param[in] size Size of area.
 */
static void convert_words(void *data, size_t size) {
	uint16_t *words_data = data;
	for (size_t i = 0; i < size; i++) {
		uint8_t *byte = (uint8_t *)&words_data[i];
		words_data[i] = byte[0] << 8 | byte[1];
	}
}

/**
 * Read a dump block.
 * @param[in] fd File descriptor.
 * @param[out] block Output block area.
 * @return 0 if EOF, -1 if error, size of read data otherwise.
 */
static ssize_t read_block(int fd, block_t *block) {
	ssize_t read_status = do_read_data(fd, block);

	if (read_status <= 0)
		return read_status;

	if (read_status < 3 * 2) {
		fprintf(stderr, "Final block has less than 3 words and is thus incomplete\n");
		return -1;
	}

	read_status /= 2;
	convert_words(block, read_status);
	read_status -= 3;
	if (block->size > read_status) {
		fprintf(stderr, "Reported block size (%" PRIu16 ") is bigger than saved data (%zd)\n", block->size, read_status);
		return -1;
	}
	// read_status holds size of block.data.
	if (read_status < 64) {
		block->checksum = block->data[read_status];
	}
	return read_status;
}

int main(int argc, char **argv) {
	if (argc != 2) {
		fprintf(stderr, "Uso: %s arquivo_de_dump\n", argv[0]);
		return -1;
	}

	block_t block;
	int fd = open(argv[1], O_RDONLY);
	if (fd == -1) {
		perror("open");
		return -1;
	}

	ssize_t read_status;
	for (read_status = read_block(fd, &block); read_status > 0;
		read_status = read_block(fd, &block)) {

		uint16_t checksum = block.start + block.size;

		printf("\tstart 0x%.4" PRIx16 "\tsize 0x%.4" PRIx16 "\n", block.start, block.size);
		for (uint16_t i = 0; i < block.size; i++) {
			printf("%.4x ", block.data[i]);
			checksum += block.data[i];
		}
		printf("\n");

		if (checksum != block.checksum) {
			fprintf(stderr, "Checksum mismatch: expected %.4" PRIx16 ", block recorded %.4" PRIx16 "\n", checksum, block.checksum);
		}

		if (block.size < 64)
			break;
	}

	close(fd);
	return read_status;
}
