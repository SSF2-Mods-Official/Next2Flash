package
{
    import flash.display.MovieClip;

    public dynamic class trail_cfalcon_utilt extends MovieClip
    {

        public function trail_cfalcon_utilt()
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

