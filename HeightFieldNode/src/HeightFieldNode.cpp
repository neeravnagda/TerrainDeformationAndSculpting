#include "HeightFieldNode.h"
#include "FastNoise.h"
//-----------------------------------------------------------------------------
MTypeID HeightField::m_id(0x1003);
const MString HeightField::typeName("HeightFieldNode");
//-----------------------------------------------------------------------------
void* HeightField::creator()
{
    return new HeightField();
}
//-----------------------------------------------------------------------------
MStatus HeightField::initialize()
{

}
//-----------------------------------------------------------------------------
void HeightField::compute(const MPlug &_plug, MDataBlock &_data)
{
  /*
  size_t numRows = m_noise.size();
  size_t numColumns = m_noise[0].size();
  for (size_t i = 0; i < numColumns; ++i)
  {
    for (size_t j = 0; j < numRows; ++j)
    {
      m_noise[i][j] = m_fastNoise.GetNoise(i, j);
    }
  }
  */
}
//-----------------------------------------------------------------------------
HeightField::HeightField()
{
}
//-----------------------------------------------------------------------------
HeightField::~HeightField()
{
}
//-----------------------------------------------------------------------------
