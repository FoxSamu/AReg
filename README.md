# A Register - an extension on Brainfuck

AReg is a superset of Brainfuck, adding an extra register next to a memory tape, which values can be copied from and to, and which can be modified itself in the same way as slots on the memory tape. In addition, AReg adds a few extra commands to print numbers and system dependent newlines.

The runtime has a "target register" and a "recipient register". The target register is used to read and write to. The recipient register is used to copy from and swap with. A the start of the program, the target register is the pointed memory register, and the recipient register is the A Register. The runtime can swap the 'target' and 'recipient' labels on command.

List of commands:
- `>` Increments the tape pointer. If the pointer falls out of the tape, the pointer is set to 0
- `<` Decrements the tape pointer. If the pointer falls out of the tape, the pointer is set to the tape end
- `+` Increments the target register. If it exceeds the maximum value (255 by default), it is set to 0
- `-` Decrements the target register. If it exceeds 0, it is set to the maximum value (255 by default)
- `,` Reads one character from the standard input, as ASCII (0 if the character is not ASCII) and store it in the target register
- `.` Prints the value in the target register as ASCII
- `[` Jumps to the matching `]` if the pointed memory register is 0
- `]` Jumps to the matching `[` if the pointed memory register is not 0
- `(` Jumps to the matching `)` if the pointed memory register equals the A Register
- `)` Jumps to the matching `(` if the pointed memory register does not equal the A Register
- `^` Flips the target register and the recipient register
- `;` Copies the value from the recipient register into the target register
- `:` Swaps the values of the recipient register and the target register
- `!` Prints the value in the target register as a decimal number
- `_` Prints a system dependent newline character (CRLF on windows, LF on MacOS and most other platforms)

In addition, AReg ignores any character between `#` and any newline character (`CR` or `LF`), allowing you to make comments with punctuation without having to care about accidentally writing extra commands. AReg still ignores any non-command character outside of comments.

## Examples

### Fibonacci sequence
This program prints the Fibonacci sequence up to 144, separated by whitespaces.

```
++++++++++>>+>+<<<[>>[>]<^;^>>;<<<^;^>>;>[<+>-]<[<]<-]^;++++++++++++++++++++++++++++++++^>>[!>^.^]
```

For an explanation, see [examples/fibonacci.areg](examples/fibonacci.areg).

### Hello world!
This program prints `Hello World!` with a newline. Almost the same as Brainfuck, except it uses the `_` instruction to print a system dependent newline.

```
++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>-[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+._
```

For an explanation, see [examples/helloworld.areg](examples/helloworld.areg).