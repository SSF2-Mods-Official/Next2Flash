// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//firefoxTrail

package 
{
    import flash.display.MovieClip;

    public dynamic class firefoxTrail extends MovieClip 
    {

        public function firefoxTrail()
        {
            addFrameScript(14, this.frame15);
        }

        internal function frame15():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}//package 

