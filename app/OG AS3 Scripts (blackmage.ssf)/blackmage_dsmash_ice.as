// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_dsmash_ice

package 
{
    import flash.display.MovieClip;

    public dynamic class blackmage_dsmash_ice extends MovieClip 
    {

        public function blackmage_dsmash_ice()
        {
            addFrameScript(16, this.frame17);
        }

        internal function frame17():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}//package 

