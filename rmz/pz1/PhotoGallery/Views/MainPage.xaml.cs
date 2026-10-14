using System.ComponentModel;
using PhotoGallery.Models;
using PhotoGallery.ViewModels;

namespace PhotoGallery.Views;

public partial class MainPage : ContentPage
{
    private readonly MainViewModel _vm;
    private bool _loaded;

    public MainPage(MainViewModel vm)
    {
        InitializeComponent();
        BindingContext = _vm = vm;
        // TableView не має ItemsSource, тому секції перебудовуються при зміні списку у ViewModel.
        _vm.PropertyChanged += OnViewModelChanged;
        Rebuild();
    }

    protected override async void OnAppearing()
    {
        base.OnAppearing();
        if (_loaded) return;
        _loaded = true;
        await _vm.LoadAsync();
    }

    private void OnViewModelChanged(object? sender, PropertyChangedEventArgs e)
    {
        if (e.PropertyName == nameof(MainViewModel.WithLocation)) Rebuild();
    }

    private void Rebuild()
    {
        var root = new TableRoot();
        var withGps = _vm.WithLocation.ToList();
        var withoutGps = _vm.WithoutLocation.ToList();
        if (withGps.Count > 0) root.Add(BuildSection($"📍 З геолокацією ({withGps.Count})", withGps));
        if (withoutGps.Count > 0) root.Add(BuildSection($"Без геолокації ({withoutGps.Count})", withoutGps));
        Gallery.Root = root;
        EmptyLabel.IsVisible = withGps.Count + withoutGps.Count == 0;
    }

    private TableSection BuildSection(string title, IEnumerable<PhotoItem> photos)
    {
        var section = new TableSection(title);
        foreach (var photo in photos) section.Add(BuildCell(photo));
        return section;
    }

    /// <summary>Рядок галереї: мініатюра, ім'я файлу, дата й камера, координати.</summary>
    private ViewCell BuildCell(PhotoItem photo)
    {
        var thumb = new Image
        {
            Source = ImageSource.FromFile(photo.FilePath),
            WidthRequest = 72,
            HeightRequest = 72,
            Aspect = Aspect.AspectFill,
        };
        var text = new VerticalStackLayout
        {
            Spacing = 2,
            VerticalOptions = LayoutOptions.Center,
            Children =
            {
                new Label { Text = photo.FileName, FontAttributes = FontAttributes.Bold, FontSize = 16 },
                new Label { Text = photo.Summary, FontSize = 13, TextColor = Colors.Gray },
                new Label { Text = photo.CoordinatesText, FontSize = 13,
                            TextColor = photo.HasLocation ? Color.FromArgb("#4f8ff7") : Colors.Gray },
            },
        };
        var row = new Grid { ColumnDefinitions = [new(72), new(GridLength.Star)], ColumnSpacing = 12, Padding = new Thickness(12, 6) };
        row.Add(thumb, 0);
        row.Add(text, 1);

        var cell = new ViewCell { View = row };
        cell.Tapped += (_, _) => _vm.OpenCommand.Execute(photo);
        cell.ContextActions.Add(new MenuItem { Text = "Видалити", IsDestructive = true, Command = _vm.RemoveCommand, CommandParameter = photo });
        return cell;
    }
}
