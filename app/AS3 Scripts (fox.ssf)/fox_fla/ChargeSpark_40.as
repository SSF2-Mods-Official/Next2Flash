// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.ChargeSpark_40

package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class ChargeSpark_40 extends MovieClip 
    {

        public function ChargeSpark_40()
        {
            addFrameScript(4, this.frame5);
        }

        internal function frame5():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}//package fox_fla

