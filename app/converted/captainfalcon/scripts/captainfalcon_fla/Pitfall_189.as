package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class Pitfall_189 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var xframe:String;
        public var self:CaptainExt;

        public function Pitfall_189()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.xframe = "pitfall";
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as CaptainExt);
                this.self.setGlobalVariable("jab", false);
                this.self.setGlobalVariable("jab2", false);
                stop();
            };
        }


    }
}

