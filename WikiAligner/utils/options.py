class Options:
    def print_options(self, options, prompt):
        """Print options as (<index>)......<option>
        """
        if prompt:
            print(prompt)

        for idx, option in enumerate(options):
            # If <option> itself has several sub-options, separate them with spaces.
            if isinstance(option, list) or isinstance(option, tuple):
                option_str = '    '.join(option)
                print(f'({idx + 1})......{option_str}')
            print(f'({idx + 1})......{option}')

    def get_option_choice(self, options, prompt: str = ''):
        """Get option choice from user input. <option index> = <user input> - 1.
        """
        if prompt:
            print(prompt)

        option_idx = int(input()) - 1
        return options[option_idx]