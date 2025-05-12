type PlainObject<T = unknown> = { [key: string]: T }
type Nested<T = unknown> = T | PlainObject<T> | Array<T>

export const toSnakeCase = <T extends Nested>(obj: T): T => {
  if (Array.isArray(obj)) {
    return obj.map(toSnakeCase) as T // Apply recursion on arrays
  } else if (obj !== null && typeof obj === 'object') {
    const transformedObj = Object.fromEntries(
      Object.entries(obj).map(([key, value]) => [
        key.replace(/([A-Z])/g, '_$1').toLowerCase(),
        toSnakeCase(value) // Apply recursion on values
      ])
    )
    return transformedObj as T // Return transformed object
  }
  return obj // Return primitive values unchanged
}

// // Example usage:
// const requestData: PassagesDocumentRequest = {
//   langCode: "en",
//   passageReferences: [
//     {
//       id: 1,
//       langCode: "en",
//       bookCode: "GEN",
//       bookName: "Genesis",
//       chapterNum: 1,
//       verseReference: "1:1-3",
//     },
//     {
//       id: 2,
//       langCode: "en",
//       bookCode: "EXO",
//       bookName: "Exodus",
//       chapterNum: 20,
//       verseReference: "1-17",
//     },
//   ],
//   emailAddress: "user@example.com",
// }

// const snakeCaseData = toSnakeCase(requestData)
// console.log(snakeCaseData)
