package
{
    import flash.display.MovieClip;

    public dynamic class saffronCityBGChars extends MovieClip
    {

        public var poke:Number;

        public function saffronCityBGChars()
        {
            super();
            addFrameScript(145, this.frame146);
        }

        internal function frame146():*
        {
            this.poke = SSF2API.random();
            if ((this.poke > 0.2) && (this.poke <= 0.4))
            {
                gotoAndStop("butterfree");
            };
            if ((this.poke > 0.4) && (this.poke <= 0.6))
            {
                gotoAndStop("fearow");
            };
            if ((this.poke > 0.6) && (this.poke <= 0.8))
            {
                gotoAndStop("pidgey");
            };
            if ((this.poke > 0.8) && (this.poke <= 1))
            {
                gotoAndStop("loop");
            };
        }


    }
}

