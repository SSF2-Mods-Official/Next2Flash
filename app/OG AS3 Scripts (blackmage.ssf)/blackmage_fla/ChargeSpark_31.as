// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.ChargeSpark_31

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class ChargeSpark_31 extends MovieClip 
    {

        public function ChargeSpark_31()
        {
            addFrameScript(4, this.frame5);
        }

        internal function frame5():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}//package blackmage_fla

