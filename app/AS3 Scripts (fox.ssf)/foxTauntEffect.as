// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//foxTauntEffect

package 
{
    import flash.display.MovieClip;

    public dynamic class foxTauntEffect extends MovieClip 
    {

        public function foxTauntEffect()
        {
            addFrameScript(13, this.frame14);
        }

        internal function frame14():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}//package 

