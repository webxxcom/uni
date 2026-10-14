namespace PhotoGallery;

public partial class AppShell : Shell
{
    public AppShell()
    {
        InitializeComponent();
        // Сторінка перегляду фото відкривається з галереї: Shell.GoToAsync(nameof(PhotoPage), параметри).
        Routing.RegisterRoute(nameof(Views.PhotoPage), typeof(Views.PhotoPage));
    }
}
