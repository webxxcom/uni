using PhotoGallery.ViewModels;

namespace PhotoGallery.Views;

public partial class PhotoPage : ContentPage
{
    public PhotoPage(PhotoViewModel vm)
    {
        InitializeComponent();
        BindingContext = vm;
    }
}
