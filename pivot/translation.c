
void pwnme(char * pivot)
{
	char buffer[0x20];
	memset(buffer, 0, 0x20);
	puts("Call ret2win() from libpivot");
	printf("The Old Gods kindly bestow upon you a place to pivot: %p\n", pivot);
	read(0, pivot, 0x100);
	puts("Thank you!\n");
	puts("Now please send your stack smash");
	printf("> ");
	read(0, buffer, 0x40);
	printf("Thank you!");
}

void uselessFunction()
{
	foothold_function();
	exit(1);
}

int main()
{
	setvbuf(stdout, 0, 2, 0);
	puts("pivot by ROP Emporium");
	puts("x86_64\n");
	char * buffer = malloc(0x1000000);
	if(buffer == NULL)
	{
		puts("Failed to request space for pivot stack");
		exit(1);
	}
	pwnme(buffer + 0xffff00);
	free(buffer);
	puts("\nExiting");
	return 0;
}
