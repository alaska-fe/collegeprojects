namespace TaskManager;

public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
    }

    private async void OnStartButtonClicked(object sender, EventArgs e)
    {
        await DisplayAlert("Готово", "Приложение готово к работе!", "OK");
    }
}
