package org.example.patterns;
public class GameIteratorTest {
    public static void main(String[] args) {
        GameCollection col = new GameCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("game:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
