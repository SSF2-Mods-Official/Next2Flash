package
{
    import flash.display.MovieClip;

    public dynamic class chibirobo_effect_lidclose extends MovieClip
    {

        public function chibirobo_effect_lidclose()
        {
            super();
            addFrameScript(11, this.frame12);
        }

        internal function frame12():*
        {
            parent.removeChild(this);
        }


    }
}

