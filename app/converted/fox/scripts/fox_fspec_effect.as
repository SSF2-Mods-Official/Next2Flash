package
{
    import flash.display.MovieClip;

    public dynamic class fox_fspec_effect extends MovieClip
    {

        public function fox_fspec_effect()
        {
            super();
            addFrameScript(8, this.frame9);
        }

        internal function frame9():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

