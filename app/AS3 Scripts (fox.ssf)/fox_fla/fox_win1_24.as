// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.fox_win1_24

package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_win1_24 extends MovieClip 
    {

        public function fox_win1_24()
        {
            addFrameScript(39, this.frame40, 66, this.frame67);
        }

        internal function frame40():*
        {
            SSF2API.playSound("fox_win2");
        }

        internal function frame67():*
        {
            this.gotoAndStop("loop");
        }


    }
}//package fox_fla

