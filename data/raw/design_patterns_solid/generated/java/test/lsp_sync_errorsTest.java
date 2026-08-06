package org.example.patterns;
public class SyncLspTest {
    public static void main(String[] args) {
        SyncShape[] arr = new SyncShape[] { new SyncRectangle(2,3), new SyncSquare(4) };
        if (SyncLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
