import type { PageLoad } from './$types'

export const load: PageLoad = ({ params }) => {
  return { lang0Code: params.lang0_code }
}
