apiIP = "localhost"

bot_token = ""

chatID = -1000000000000

start_msg = (
    "Привет! Я - бот, генерирующий картин очки на пекарне Гроба.\n" +
    "Напиши /help для справки."
)

help_msg = (
    "Вот список доступных команд:\n\n" +
    "<b>/start</b> - начать работу с ботом\n\n" + 
    "<b>/help</b> - получить справку\n\n" +
    "<b>/config option &lt;var&gt;</b> - конфигурация Stable Diffusion\n\n" +
    "   current - посмотреть текущую конфигурацию\n\n" +
    "   default - сбросить конфиг к настройкам по умолчанию\n\n" +
	"   hr &lt;enable/disable&gt; - включение апскейлера (по умолчанию enable)\n" +
    "   upscaler &lt;Latent/ESRGAN_4x&gt; - выбор апскейлера (по умолчанию Latent)\n" +
	"   hr_scale &lt;1.0 -&gt; 2.0&gt; - множитель разрешения апскейлера (по умолчанию 2.0)\n" +
	"   seed &lt;var/random&gt; - сид для генерации изображения (по умолчанию random)\n" +
	"   width &lt;128 -&gt; 512&gt; - ширина изображения (по умолчанию 512)\n" +
	"   height &lt;128 -&gt; 512&gt; - высота изображения (по умолчанию 512)\n" +
	"   strength &lt;0 -&gt; 20&gt; - приоритет соответствия промпту (по умолчанию 7)\n" +
	"   steps &lt;1 -&gt; 50&gt; - количество шагов генерации (по умолчанию 20)\n\n" +
    "<b>/generate &lt;prompt&gt;</b> - генерация изображения"
)

aftergen_msg = (
    "Что-то не работает? Есть предложения? Обращайтесь к @zuGR0B и @MrJefter"
)

generr_msg = (
    "Не получен ответ от API, попробуйте ещё раз."
)

gentimeout_msg = (
    "Возникла ошибка соединения с API, попробуйте ещё раз"
)

tokensne_msg = (
    "Увы, но у вас закончились токены\n\n" + 
    "Но, так как это лишь тестовая версия бота - токены восстановлены до 100" + 
    " и будут восстанавливаться автоматически, пока тестирование бота не будет завершено.\n" +
    "Попробуйте сгенерировать изображение ещё раз."
)

high_resolutionD = True
hr_scaleD = 2.00
seedD = -1
widthD = 512
heightD = 512
prompt_strengthD = 7
stepsD = 20
tokensD = 10
upscalerD = "Latent"

if __name__ == "__main__":
    print("This one is just a config, you need to run TGBot.py")