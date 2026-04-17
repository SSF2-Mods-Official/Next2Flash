// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blasterhit

package 
{
    import flash.display.MovieClip;

    public dynamic class blasterhit extends MovieClip 
    {

        public function blasterhit()
        {
            addFrameScript(4, this.frame5);
        }

        internal function frame5():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}//package 

