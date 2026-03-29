package
{
    import flash.display.MovieClip;

    public dynamic class trail_cfalcon_jab1 extends MovieClip
    {

        public function trail_cfalcon_jab1()
        {
            super();
            addFrameScript(3, this.frame4);
        }

        internal function frame4():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

