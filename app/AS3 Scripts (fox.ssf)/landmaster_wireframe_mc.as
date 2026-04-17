// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//landmaster_wireframe_mc

package 
{
    import flash.display.MovieClip;

    public dynamic class landmaster_wireframe_mc extends MovieClip 
    {

        public function landmaster_wireframe_mc()
        {
            addFrameScript(40, this.frame41);
        }

        internal function frame41():*
        {
            if (parent != null)
            {
                parent.removeChild(this);
            };
        }


    }
}//package 

