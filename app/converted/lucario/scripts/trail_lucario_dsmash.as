package
{
    import flash.display.MovieClip;

    public dynamic class trail_lucario_dsmash extends MovieClip
    {

        public function trail_lucario_dsmash()
        {
            super();
            addFrameScript(3, this.frame4);
        }

        internal function frame4():*
        {
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

