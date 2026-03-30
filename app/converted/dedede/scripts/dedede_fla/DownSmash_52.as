package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class DownSmash_52 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;
        public var xframe:String;

        public function DownSmash_52()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 44, this.frame45, 45, this.frame46, 47, this.frame48, 51, this.frame52, 64, this.frame65);
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-4),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
        }

        internal function frame5():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame45():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame46():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
        }

        internal function frame48():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_swing_ll");
            this.self.playSound("ssf2_snd_sfx_dedede_smash");
            this.self.playVoiceSound(1);
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-10),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
            SSF2API.getCamera().shake(4);
        }

        internal function frame52():*
        {
            SSF2API.getCamera().shake(4);
        }

        internal function frame65():*
        {
            this.self.endAttack();
        }


    }
}

