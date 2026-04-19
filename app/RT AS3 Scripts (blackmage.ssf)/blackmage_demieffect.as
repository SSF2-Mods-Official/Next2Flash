// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_demieffect

package 
{
    import flash.display.MovieClip;

    public dynamic class blackmage_demieffect extends MovieClip 
    {

        public function blackmage_demieffect()
        {
            addFrameScript(17, this.frame18);
        }

        internal function frame18():*
        {
            stop();
            if (parent != null)
            {
                parent.removeChild(this);
            };
        }


    }
}//package 

