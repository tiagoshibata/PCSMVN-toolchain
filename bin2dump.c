#include <fcntl.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#define BLOCK_DATA_SIZE			(64 * 2)
#define BLOCK_CONTROL_SIZE	(3 * 2)
/// Space for data words and start address, size and checksum.
#define BLOCK_SIZE					(BLOCK_DATA_SIZE + BLOCK_CONTROL_SIZE)

typedef struct {
	uint16_t start;
	uint16_t size;
	uint16_t data[64];
	uint16_t checksum;
} block_t;

static ssize_t do_read_data(int fd, void *block) {
	ssize_t data_read = 0;

	while (data_read < BLOCK_DATA_SIZE) {
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

int main(int argc, char **argv) {
	if (argc != 3) {
		fprintf(stderr, "Uso: %s arquivo_bin arquivo_dump\n", argv[0]);
		return -1;
	}

	int bin = open(argv[1], O_RDONLY);
	if (bin == -1) {
		perror("open");
		return -1;
	}

	int dump = open(argv[2], O_WRONLY | O_CREAT | O_TRUNC, S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP);
	if (dump == -1) {
		perror("open");
		return -1;
	}

	ssize_t read_status, position = 0;
	block_t block;
	for (read_status = do_read_data(bin, &block.data); read_status > 0;
		read_status = do_read_data(bin, &block.data)) {

		if (read_status & 1) {
			fprintf(stderr, "Odd size data is invalid\n");
			break;
		}

		block.start = position;
		block.size = read_status / 2;
		uint16_t checksum = block.start + block.size;

		convert_words(&block.data, block.size);
		for (uint16_t i = 0; i < block.size; i++)
			checksum += block.data[i];
		block.data[block.size] = checksum;

		convert_words(&block, read_status + BLOCK_CONTROL_SIZE);
		if (write(dump, &block, read_status + BLOCK_CONTROL_SIZE) != read_status + BLOCK_CONTROL_SIZE) {
			perror("write");
			break;
		}

		position += read_status;
	}

	if (read_status < 0)
		perror("read");

	close(bin);
	close(dump);
	return read_status;
}
