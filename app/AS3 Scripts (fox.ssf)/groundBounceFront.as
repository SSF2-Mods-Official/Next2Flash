// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//groundBounceFront

package 
{
    import flash.display.MovieClip;

    public dynamic class groundBounceFront extends MovieClip 
    {

        public function groundBounceFront()
        {
            addFrameScript(9, this.frame10);
        }

        internal function frame10():*
        {
            stop();
            if (((!(root == null)) && (!(parent == null))))
            {
                parent.removeChild(this);
            };
        }


    }
}//package 

