import { describe, expect, it } from "vitest";
import { createTranslator } from "../i18n";
import { moduleFamilySummary } from "./moduleFamilySummary";

describe("moduleFamilySummary", () => {
  const t = createTranslator("en");

  it("reports a fully loaded unfiltered family", () => {
    expect(
      moduleFamilySummary(
        {
          filtered: false,
          loadedCount: 2,
          sourceCount: 7,
          totalCount: 2,
          visibleCount: 2,
        },
        t,
      ),
    ).toBe("2 objects · 7 family source files");
  });

  it("distinguishes visible rows from the complete family", () => {
    expect(
      moduleFamilySummary(
        {
          filtered: true,
          loadedCount: 2,
          sourceCount: 7,
          totalCount: 2,
          visibleCount: 1,
        },
        t,
      ),
    ).toBe("1 of 2 objects shown · 7 family source files");
  });

  it("distinguishes a loaded Catalog page from the complete family", () => {
    expect(
      moduleFamilySummary(
        {
          filtered: false,
          loadedCount: 60,
          sourceCount: 10_204,
          totalCount: 301,
          visibleCount: 60,
        },
        t,
      ),
    ).toBe("60 of 301 objects loaded · 10204 family source files");
  });

  it("reports filtering and paging together without overstating coverage", () => {
    expect(
      moduleFamilySummary(
        {
          filtered: true,
          loadedCount: 60,
          sourceCount: 10_204,
          totalCount: 301,
          visibleCount: 12,
        },
        t,
      ),
    ).toBe("12 shown from 60 loaded of 301 objects · 10204 family source files");
  });

  it("normalizes inconsistent asynchronous counts", () => {
    expect(
      moduleFamilySummary(
        {
          filtered: false,
          loadedCount: 1,
          sourceCount: Number.NaN,
          totalCount: 1,
          visibleCount: 2,
        },
        t,
      ),
    ).toBe("2 objects · 0 family source files");
  });
});
