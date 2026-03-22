
// usefulString address: 0x601060
const char * usefulString = "/bin/cat flag.txt";

//usefulFunction address: 0x400742
void usefulFunction()
{
	system("/bin/ls");
}

void pwnme()
{
	char buffer[32];
	memset(buffer, 0, 32);
	puts("Contriving a reason to ask user for data...");
	printf("> ");
	read(0, buffer, 96);
	puts("Thank you!");

}

int main(int argc, char** argv)
{
	setvbuf(stdout, 0, 2, 0);
	puts("split by ROP Emporium");
	puts("x86_64\n");
	pwnme();
	puts("\nExiting");
	return 0;
}
