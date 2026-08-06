package org.example.patterns;
public class SearchCompositeTest {
    public static void main(String[] args) {
        SearchComposite root = new SearchComposite();
        root.add(new SearchLeaf(2));
        root.add(new SearchLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
