
void callme_one(int x, int y, int z)
{
	// jump to libcallme.so	
}

void callme_two(int x, int y, int z)
{
	// jump to libcallme.so
}

void callme_three(int x, int y, int z)
{
	// jump to libcallme.so
}

void usefulGadgets()
{
	// pop rdi
	// pop rsi
	// pop rdx
}

void usefulFunction()
{
	callme_three(4, 5, 6);
	callme_two(4, 5, 6);
	callme_one(4, 5, 6);
	exit(1);
}

void pwnme()
{
	char buffer[32];
	memset(buffer, 0, 32);
	puts("Hope you read the instructions...\n");
	printf("> ");
	read(0, buffer, 512);
	puts("Thank you!");
}

int main(int argc, char** argv)
{
	setvbuf(stdout, 0, 2, 0);
	puts("callme by ROP Emporium");
	puts("x86_64\n");
	pwnme();
	puts("\nExiting");

	return 0;
}
