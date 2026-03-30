package
{
    import flash.display.MovieClip;

    public dynamic class trail_lucario_getup2 extends MovieClip
    {

        public function trail_lucario_getup2()
        {
            super();
            addFrameScript(7, this.frame8);
        }

        internal function frame8():*
        {
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

