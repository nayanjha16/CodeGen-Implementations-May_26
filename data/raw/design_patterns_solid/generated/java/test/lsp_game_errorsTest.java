package org.example.patterns;
public class GameLspTest {
    public static void main(String[] args) {
        GameShape[] arr = new GameShape[] { new GameRectangle(2,3), new GameSquare(4) };
        if (GameLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
