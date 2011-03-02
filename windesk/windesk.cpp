/*
windesk: Changes windows desktop wallpaper in commandline.

Copyright (c) 2009 by Yanglei Zhao
http://www4.ncsu.edu/~yzhao11/
z12y12l12@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA.
*/

/*
	VERSION = 1.1.0
*/
#include <stdio.h>
#include <direct.h>
#include <windows.h>
#include <gdiplus.h>

WCHAR destFilename[256]; //The destination file created for desktop.

BOOL IsVistaOrLater(){
	OSVERSIONINFO osversion;
	ZeroMemory(&osversion, sizeof(OSVERSIONINFO));
	osversion.dwOSVersionInfoSize = sizeof(OSVERSIONINFO);

	GetVersionEx(&osversion);

	return (osversion.dwMajorVersion >= 6);
}

INT GetEncoderClsid(const WCHAR* format, CLSID* pClsid){
	UINT num = 0; // number of encoders
	UINT size = 0; // size of encoder
	Gdiplus::ImageCodecInfo *pImageCodecInfo = NULL;
	Gdiplus::GetImageEncodersSize(&num, &size);

	if(size == 0){
		wprintf(L"GetImageEncodersSize failed.\n");
		return -1;
	}

	pImageCodecInfo = (Gdiplus::ImageCodecInfo *)(malloc(size));

	if(pImageCodecInfo == NULL){
		wprintf(L"Allocate memory failed, size %d.\n", size);
		return -1;
	}

	Gdiplus::GetImageEncoders(num, size, pImageCodecInfo);

	for(UINT i = 0; i < num; i++){
		if(wcscmp(pImageCodecInfo[i].MimeType, format) == 0){
			*pClsid = pImageCodecInfo[i].Clsid;
			free(pImageCodecInfo);
			return 0;
		}
	}


	free(pImageCodecInfo);
	wprintf(L"Load encoder failed.\n");
	return -1; // failure
}

INT GetDestFilename(WCHAR *fname_ret, const WCHAR *name){
	wcscpy(fname_ret, _wgetenv(L"AppData"));

	wcscat(fname_ret, L"\\windesk\\");
	// Make dir of the destination file on the way.
	_wmkdir(fname_ret);
	wcscat(fname_ret, name);
	return 0;
}

/* We need to save the picture defined as jpg in windows vista+ or bmp in windows xp- */
INT SaveAs(WCHAR *inputFile){
	// Initiallizing GDI+
	ULONG_PTR gdiplusToken;
	Gdiplus::GdiplusStartupInput gdiplusStartupInput;
	Gdiplus::GdiplusStartup(&gdiplusToken, &gdiplusStartupInput, NULL);

	// Load image
	Gdiplus::Image *image = new Gdiplus::Image(inputFile);

	// If we fail on this task. (Image file does not exist, or so...)
	if(!image->GetWidth()){
		wprintf(L"Load image failed.\n");
		return -1; // Failure
	}

	// Make dir for

	// Load encoder, Get the destination filename, and save!
	CLSID encoderClsid;

	Gdiplus::Status stat;

	if(IsVistaOrLater()){

		if(GetEncoderClsid(L"image/jpeg", &encoderClsid)){
			return -1;
		}
		GetDestFilename(destFilename, L"wallpaper.jpg");

		// Set encoder parameters for jpg file
		Gdiplus::EncoderParameters encoderParameters;
		ULONG quality = 100;
		encoderParameters.Count = 1;
		encoderParameters.Parameter[0].Guid = Gdiplus::EncoderQuality;
		encoderParameters.Parameter[0].Type = Gdiplus::EncoderParameterValueTypeLong;
		encoderParameters.Parameter[0].NumberOfValues = 1;
		encoderParameters.Parameter[0].Value = &quality;

		stat = image->Save(destFilename, &encoderClsid, &encoderParameters);
	}
	else{
		GetEncoderClsid(L"image/bmp", &encoderClsid);
		GetDestFilename(destFilename, L"wallpaper.bmp");
		stat = image->Save(destFilename, &encoderClsid, NULL);
	}

	if(stat != Gdiplus::Ok){
		wprintf(L"Save image failed.\n", destFilename);
	}

	delete image;
	Gdiplus::GdiplusShutdown(gdiplusToken);
	return 0;
}

INT main(void){
	INT argc;
	WCHAR **argv = CommandLineToArgvW(GetCommandLineW(), &argc);

	// If we do not have 2 parameters, that's wrong.
	if(argc != 2){
		wprintf(L"Usage: %s [filename]\n", argv[0]);
		return 1;
	}
	SaveAs(argv[1]);

	// Set desktop wallpaper using windows api
	SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, destFilename, 0);
	return 0;
}
