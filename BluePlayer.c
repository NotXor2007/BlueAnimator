//> <
#include<SDL2/SDL.h>
#include<stdio.h>

SDL_Window *window;
SDL_Surface *surface;
FILE *filePtr;
SDL_Event event;
unsigned char fps;
unsigned short width, height;

typedef struct
{
	unsigned char r;
	unsigned char g;
	unsigned char b;
	unsigned char a;
} Color;

void FillPixels(SDL_Surface* surface)
{
	SDL_LockSurface(surface);
	Color pixcolor = {0,0,0,0};
	unsigned char tempbyte;
	if(filePtr == NULL);
	for(int pixy = 0;pixy < height;pixy++)
	{
		for(int pixx = 0;pixx < width;pixx++)
		{
			fread(&(pixcolor.r),sizeof(unsigned char),1,filePtr);
			fread(&(pixcolor.g),sizeof(unsigned char),1,filePtr);
			fread(&(pixcolor.b),sizeof(unsigned char),1,filePtr);
			fread(&(pixcolor.a),sizeof(unsigned char),1,filePtr);
			*((char*)(*surface).pixels + pixx*4 + pixy * surface->pitch + 0) = pixcolor.b;
			*((char*)(*surface).pixels + pixx*4 + pixy * surface->pitch + 1) = pixcolor.g;
			*((char*)(*surface).pixels + pixx*4 + pixy * surface->pitch + 2) = pixcolor.r;
			*((char*)(*surface).pixels + pixx*4 + pixy * surface->pitch + 3) = pixcolor.a;
		}
	}
	fread(&tempbyte,sizeof(unsigned char),1,filePtr);
	if(feof(filePtr))
		fseek(filePtr,5,SEEK_SET);
	else fseek(filePtr,-1,SEEK_CUR);
	SDL_UnlockSurface(surface);
}


void ReadHeader(int argc, char **argv)
{
	unsigned char temp;
	width = 0;height = 0;
	if(argc != 2) exit(0x01);
	filePtr = fopen(argv[1],"r");
	if(filePtr == NULL) exit(0x02);
	fread(&fps,sizeof(unsigned char),1,filePtr);
	for(char i = 1; i >= 0;i--)
	{
		fread(&temp,sizeof(unsigned char),1,filePtr);
		width += temp << 8*i;
	}
	for(char i = 1; i >= 0;i--)
	{
		fread(&temp,sizeof(unsigned char),1,filePtr);
		height += temp << 8*i;
	}
}

int main(int argc, char **argv)
{
	SDL_Init(SDL_INIT_VIDEO);
	ReadHeader(argc, argv);
	window = SDL_CreateWindow("BluePlayer - 1.0",SDL_WINDOWPOS_CENTERED,SDL_WINDOWPOS_CENTERED,width,height,0);
	surface = SDL_GetWindowSurface(window);
	//Test
	while(1)
	{
		while(SDL_PollEvent(&event))
		{
			switch(event.type)
			{
				case SDL_QUIT:
					goto Exit;
			}
		}
		surface = SDL_GetWindowSurface(window);
		FillPixels(surface);	
		SDL_UpdateWindowSurface(window);
	}
	Exit:
	fclose(filePtr);
	SDL_DestroyWindow(window);	
	SDL_Quit();
	return 0;
}


