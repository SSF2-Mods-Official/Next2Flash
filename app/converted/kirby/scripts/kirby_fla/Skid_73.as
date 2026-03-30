package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class Skid_73 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var fatland:Boolean;

        public function Skid_73()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 8, this.frame9, 14, this.frame15);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.fatland = false;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("kirbyPeachUsed", false);
                this.self.playSound("ssf2_snd_sfx_kirby_run_stop");
            };
        }

        internal function frame8():*
        {
            this.self.endAttack();
        }

        internal function frame9():*
        {
            this.fatland = true;
        }

        internal function frame15():*
        {
            this.self.endAttack();
        }


    }
}

