package
{
    import flash.display.MovieClip;

    public dynamic class trail_cfalcon_ftilt extends MovieClip
    {

        public function trail_cfalcon_ftilt()
        {
            super();
            addFrameScript(6, this.frame7);
        }

        internal function frame7():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

