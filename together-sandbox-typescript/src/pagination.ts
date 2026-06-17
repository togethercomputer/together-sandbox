/**
 * Cursor-based pagination support.
 *
 * List endpoints return a {@link Page}, which holds one page of results
 * (`data` + `nextCursor`) and is itself async-iterable across *all* remaining
 * pages. The common case — iterate every item — needs no cursor handling:
 *
 * ```ts
 * for await (const snapshot of await sdk.snapshots.list()) {
 *   console.log(snapshot.id);
 * }
 * ```
 *
 * Page-by-page control is available when the cursor matters:
 *
 * ```ts
 * let page = await sdk.snapshots.list({ limit: 50 });
 * while (page.hasNextPage()) {
 *   console.log(page.data, page.nextCursor);
 *   page = await page.getNextPage();
 * }
 * ```
 */
export class Page<T> implements AsyncIterable<T> {
  /** Items in this page. */
  readonly data: T[];
  /** Cursor for the next page, or `null` when this is the last page. */
  readonly nextCursor: string | null;
  /** Fetches a page starting at the given cursor (undefined ⇒ first page). */
  private readonly _fetch: (cursor?: string) => Promise<Page<T>>;

  constructor(
    data: T[],
    nextCursor: string | null,
    fetch: (cursor?: string) => Promise<Page<T>>,
  ) {
    this.data = data;
    this.nextCursor = nextCursor;
    this._fetch = fetch;
  }

  /** Whether a further page exists. */
  hasNextPage(): boolean {
    return this.nextCursor !== null;
  }

  /**
   * Fetch the next page.
   *
   * @throws if called when {@link hasNextPage} is `false`.
   */
  async getNextPage(): Promise<Page<T>> {
    if (this.nextCursor === null) {
      throw new Error(
        "No next page: getNextPage() called on the last page. " +
          "Guard with hasNextPage() before calling.",
      );
    }
    return this._fetch(this.nextCursor);
  }

  /**
   * Iterate every item across all pages, fetching subsequent pages on demand.
   */
  async *[Symbol.asyncIterator](): AsyncIterator<T> {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    let page: Page<T> = this;
    for (;;) {
      for (const item of page.data) {
        yield item;
      }
      if (!page.hasNextPage()) {
        return;
      }
      page = await page.getNextPage();
    }
  }
}
