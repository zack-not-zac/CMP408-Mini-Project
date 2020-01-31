#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <string.h>
#include <time.h>

#include"piio.h"

gpio_pin apin;
lkm_data lkmdata;

void delay(int number_of_seconds) {
    //code from: https://www.geeksforgeeks.org/time-delay-c/
    // Converting time into milli_seconds 
    int milli_seconds = 1000 * number_of_seconds; 
  
    // Stroing start time 
    clock_t start_time = clock(); 
  
    // looping till required time is not acheived 
    while (clock() < start_time + milli_seconds) 
        ; 
} 

void write_to_driver(int fd) {
	int ret;
	/* Write to kernel space - see dmesg command*/
	strcpy(lkmdata.data, "This is from user application");
	lkmdata.len = 32;
	lkmdata.type = 'w';
	ret = ioctl(fd, IOCTL_PIIO_WRITE, &lkmdata);

	if (ret < 0) {
		printf("Function failed:%d\n", ret);
		exit(-1);
	}

}

void read_from_driver(int fd) {
	int ret;

	/*Read from kernel space - see dmesg command*/
	strcpy(lkmdata.data, "");
	ret = ioctl(fd, IOCTL_PIIO_READ, &lkmdata);

	if (ret < 0) {
		printf("Function failed:%d\n", ret);
		exit(-1);
	}

	printf("Message from driver: %s\n", lkmdata.data);
}

int main(int argc, char *argv[]) {
	int fd;

	fd = open("//dev//piiodev", O_RDWR);
	if (fd < 0) {
		printf("Can't open device file: %s\n", DEVICE_NAME);
		exit(-1);
	}

	if (argc > 1) {
		if (!strncmp(argv[1], "readmsg", 8)) {
			read_from_driver(fd);

		}

		if (!strncmp(argv[1], "writemsg", 9)) {
			write_to_driver(fd);
		}

		if (!strncmp(argv[1], "readpin", 8)) {
			/*  Pass GPIO struct with IO control */
			printf("Usage: readpin [pin]\n\n");
			if (argc < 3)
			{
				exit(0);
			}
			memset(&apin , 0, sizeof(apin));
			apin.pin =  strtol (argv[2],NULL,10);
			/* Pass 'apin' struct to 'fd' with IO control*/
			int ret = ioctl(fd, IOCTL_PIIO_GPIO_READ, &apin);
			strcpy(apin.desc,"ReadOpt");
			read_from_driver(fd);
			if (ret == 0)
			{
				printf("Function returned code: %d (Success)\n",ret);
			}
			else
			{
				printf("Function returned code: %d (Failed)\n", ret);
			}
			printf("READ:Requested  pin:%i - val:%i - desc:%s\n" , apin.pin , apin.value, apin.desc);
		}

		if (!strncmp(argv[1], "writepin", 9)) {
			/*  Pass GPIO struct with IO control */
			printf("Usage: writepin [pin] [value (1/0)]\n\n");
			if (argc < 3)
			{
				exit(0);
			}
			memset(&apin , 0, sizeof(apin));
			apin.pin =  strtol (argv[2],NULL,10);
			apin.value = strtol (argv[3],NULL,10);
			strcpy(apin.desc,"WriteOpt");
			/* Pass 'apin' struct to 'fd' with IO control*/
			int ret = ioctl(fd, IOCTL_PIIO_GPIO_WRITE, &apin);
			write_to_driver(fd);
			if (ret == 0)
			{
				printf("Function returned code: %d (Success)\n",ret);
			}
			else
			{
				printf("Function returned code: %d (Failed)\n", ret);
			}
			
			printf("WRITE:Requested pin:%i - val:%i - desc:%s\n" , apin.pin , apin.value, apin.desc);
		}

        if (!strncmp(argv[1], "togglepin", 10)) {
            int i = 0;
            int interval = 0;
			int ret;
            printf("Usage: togglepin [pin] [interval(milliseconds)] [no. of toggles]\n\n");
			if (argc < 4)
			{
				exit(0);
			}
            /*  Pass GPIO struct with IO control */
			memset(&apin , 0, sizeof(apin));
			i = strtol(argv[4],NULL,10);
            interval = strtol(argv[3],NULL,10);
			apin.pin =  strtol (argv[2],NULL,10);
			/* Pass 'apin' struct to 'fd' with IO control*/
			ret = ioctl(fd, IOCTL_PIIO_GPIO_READ, &apin);
			read_from_driver(fd);
			if (ret != 0)
			{
				printf("Read function returned code: %d (Failed)\n",ret);
				exit(0);
			}
			strcpy(apin.desc,"ToggleOpt");
            for(int counter = 0; counter < i; counter++)
            {
                if (apin.value == 1)
                {
                    apin.value = 0;
                }
                else
                {
                    apin.value = 1;
                }
				ret = ioctl(fd, IOCTL_PIIO_GPIO_WRITE, &apin);
				write_to_driver(fd);
				if (ret != 0)
				{
					printf("Write function returned code: %d (Failed)\n",ret);
					exit(0);
				}
			    printf("TOGGLE:Requested pin:%i - val:%i - desc:%s\n" , apin.pin , apin.value, apin.desc);
                delay(interval);
            }
        }
	}
	close(fd);
	return 0;
}
