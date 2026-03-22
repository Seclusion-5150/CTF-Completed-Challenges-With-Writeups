void ret2win()
{
	puts("Well done! Here's your flag!");
	system("/bin/cat flag.txt");
}

void pwnme()
{
	char buffer[32];
	memset(buffer, 0, 32);
	puts("For my first trick, I will attempt to fit 56 bytes of user input into 32 bytes of stack buffer!");
	puts("What could possibly go wrong?");
	puts("You there, may I have your input please? And don't worry about null bytes, we're using read()!\n");
	printf("> ");
	read(0, buffer, 56);
	puts("Thank you!");
}

int main(int argc, char** argv)
{
	setvbuf(stdout, 0, 2, 0);
	puts("ret2win by ROP Emporium");
	puts("x86_64\n");
	pwnme();
	puts("\nExiting")
	return 0;
}
