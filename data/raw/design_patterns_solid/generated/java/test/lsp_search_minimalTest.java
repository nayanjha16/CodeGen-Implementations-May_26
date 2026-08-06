package org.example.patterns;
public class SearchLspTest {
    public static void main(String[] args) {
        SearchShape[] arr = new SearchShape[] { new SearchRectangle(2,3), new SearchSquare(4) };
        if (SearchLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
