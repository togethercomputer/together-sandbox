import { describe, it, expect, vi } from "vitest";
import { Page } from "./pagination.js";

/**
 * Build a chain of Pages backed by a fake fetcher that serves fixed pages
 * keyed by cursor. Returns the first page plus a spy on the fetcher so tests
 * can assert lazy fetching.
 */
function makePages(pages: { data: number[]; nextCursor: string | null }[]) {
  const fetch = vi.fn(async (cursor?: string): Promise<Page<number>> => {
    const index = cursor === undefined ? 0 : Number(cursor);
    const p = pages[index];
    return new Page<number>(p.data, p.nextCursor, fetch);
  });
  return { first: () => fetch(), fetch };
}

describe("Page", () => {
  it("exposes data and nextCursor for the current page", async () => {
    const { first } = makePages([{ data: [1, 2], nextCursor: "1" }]);
    const page = await first();
    expect(page.data).toEqual([1, 2]);
    expect(page.nextCursor).toBe("1");
    expect(page.hasNextPage()).toBe(true);
  });

  it("reports no next page on the last page", async () => {
    const { first } = makePages([{ data: [1], nextCursor: null }]);
    const page = await first();
    expect(page.hasNextPage()).toBe(false);
    await expect(page.getNextPage()).rejects.toThrow(/No next page/);
  });

  it("getNextPage fetches the page at nextCursor", async () => {
    const { first } = makePages([
      { data: [1], nextCursor: "1" },
      { data: [2], nextCursor: null },
    ]);
    const page1 = await first();
    const page2 = await page1.getNextPage();
    expect(page2.data).toEqual([2]);
    expect(page2.hasNextPage()).toBe(false);
  });

  it("async-iterates every item across all pages", async () => {
    const { first } = makePages([
      { data: [1, 2], nextCursor: "1" },
      { data: [3], nextCursor: "2" },
      { data: [4, 5], nextCursor: null },
    ]);
    const collected: number[] = [];
    for await (const item of await first()) {
      collected.push(item);
    }
    expect(collected).toEqual([1, 2, 3, 4, 5]);
  });

  it("fetches subsequent pages lazily during iteration", async () => {
    const { first, fetch } = makePages([
      { data: [1], nextCursor: "1" },
      { data: [2], nextCursor: null },
    ]);
    const page = await first();
    expect(fetch).toHaveBeenCalledTimes(1); // only the first page so far

    const iterator = page[Symbol.asyncIterator]();
    await iterator.next(); // yields 1 from the in-hand page — no fetch yet
    expect(fetch).toHaveBeenCalledTimes(1);

    await iterator.next(); // exhausts page 1 → fetches page 2
    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it("iterates a single-page result without extra fetches", async () => {
    const { first, fetch } = makePages([{ data: [1, 2], nextCursor: null }]);
    const collected: number[] = [];
    for await (const item of await first()) {
      collected.push(item);
    }
    expect(collected).toEqual([1, 2]);
    expect(fetch).toHaveBeenCalledTimes(1);
  });
});
