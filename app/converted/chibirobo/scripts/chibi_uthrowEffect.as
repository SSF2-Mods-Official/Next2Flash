package
{
    import flash.display.MovieClip;

    public dynamic class chibi_uthrowEffect extends MovieClip
    {

        public function chibi_uthrowEffect()
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

