# Застосунок Instagram Killer (Team 4)

Застосунок "Instagram Killere" - інноваційна платформа з безпечною аутентифікацією через JWT токени та різними ролями для користувачів. Завантажуйте, редагуйте та видаляйте світлини, додавайте теги та отримуйте унікальні QR-коди для трансформованих зображень. Надавайте коментарі, відкривайте свої профілі та здійснюйте пошук за ключовими словами та тегами. Рейтинг та можливість модерування роблять цю платформу ідеальним місцем для спільного обміну фотографіями та взаємодії.

![Logo](https://github.com/Dishalex/Infinity/blob/dev/Documentation/logo.jpg)

Photo by [Izabel](https://unsplash.com/@peacelily234?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText")

## Зміст
- [Особливості](#особливості)
- [Usage](#usage)
- [Commands](#commands)
- [Examples](#examples)
- [Installation](#installation)
- [License](#license)

## Особливості
- Завантажуйте, редагуйте та видаляйте світлини
- Додавайте теги та отримуйте унікальні QR-коди для трансформованих зображень
- Надавайте коментарі, відкривайте свої профілі та здійснюйте пошук за ключовими словами та тегами
- Рейтинг та можливість модерування роблять цю платформу ідеальним місцем для спільного обміну фотографіями та взаємодії.

## Usage
To get started, clone this repository and follow the installation instructions in the [Installation](#installation) section.

## Commands

| Command Syntax           | Description                                                               |
|--------------------------|---------------------------------------------------------------------------|
| hello                    | Show a friendly greeting.                                                 |
| help                     | Display a help message with available commands.                           |
| add {name}               | Add a new contact record.                                                 |
| add {name} {data}        | Add details like birthday, phone, or email.                               |
| change {name} {data}     | Change contact data.                                                      |
| delete {name}            | Delete a contact record.                                                  |
| delete {name}  {data}    | Delete specific data from a contact.                                      |
| search {name}            | Search for contact record(s).                                             |
| show all                 | Show all contact records in a browsing mode.                              |
| show page {page_#}       | Go to page # of the adress book.                                          |
| show phones {name}       | List phones associated with a contact.                                    |
| show emails {name}       | List emails associated with a contact.                                    |
| show birthday {name}     | Show birthday of a contact.                                               |
| birthdays in {#_of_days} | Display all birthdays in the next # of days.                              |
| note                     | Enter the note taking mode                                                |
| show all                 | (in the note taking mode) Show all notes and their tags in browsing mode. |
| add note {name} {tags}   | (in the note taking mode) Add a new note.                                 |
| delete note {name}       | (in the note taking mode) Delete an existing note.                        |
| edit note {name}         | (in the note taking mode) Edit an existing note in a text editor.         |
| edit tags {name}         | (in the note taking mode) Edit tags via cli interface.                    |
| search name {name}       | (in the note taking mode) Search for notes by name.                       |
| search tags {name}       | (in the note taking mode) Search for notes by tag.                        |

## Examples

For more details and examples, please refer to the [documentation](./Documentation/).

## Installation

1. Clone the repository:
 ```bash
git clone https://github.com/your-username/python-cli-assistant.git
cd python-cli-assistant
```
2. Install dependancies:

```bash
pip install -r requirements.txt
```

3. Run the Python CLI Assistant:

```bash
python assistant.py
```

## License

This project is licensed under the MIT License.

## Contributors
- [Oleksandr Dyshliuk](https://github.com/Dishalex)
- [Dmytro Kruhlov](https://github.com/Dmytro-Kruhlov)
- [Michael Ivanov](https://github.com/MikeIV2007)
- [Artem Dorofeev](https://github.com/artem-dorofeev)
- [Igor Yevtushenko](https://github.com/II-777)
