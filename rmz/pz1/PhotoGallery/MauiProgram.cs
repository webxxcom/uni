using Microsoft.Extensions.Logging;
using PhotoGallery.Services;
using PhotoGallery.ViewModels;
using PhotoGallery.Views;

namespace PhotoGallery;

public static class MauiProgram
{
	public static MauiApp CreateMauiApp()
	{
		var builder = MauiApp.CreateBuilder();
		builder
			.UseMauiApp<App>()
			.ConfigureFonts(fonts =>
			{
				fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
				fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
			});

		// MVVM: сервіс, ViewModel-і та сторінки створює контейнер залежностей.
		builder.Services.AddSingleton<ExifService>();
		builder.Services.AddSingleton<MainViewModel>();
		builder.Services.AddSingleton<MainPage>();
		builder.Services.AddTransient<PhotoViewModel>();
		builder.Services.AddTransient<PhotoPage>();

#if DEBUG
		builder.Logging.AddDebug();
#endif

		return builder.Build();
	}
}
