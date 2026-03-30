package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class UpSmash_49 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var attackBox4:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;
        public var xframe:String;

        public function UpSmash_49()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 44, this.frame45, 45, this.frame46, 48, this.frame49, 52, this.frame53, 53, this.frame54, 68, this.frame69);
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

        internal function frame49():*
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
        }

        internal function frame53():*
        {
            SSF2API.getCamera().shake(5);
            this.self.playSound("ssf2_snd_sfx_dedede_swing_land");
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame54():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l2");
            }
            else
            {
                this.self.playSound("dedede_step2");
            };
        }

        internal function frame69():*
        {
            this.self.endAttack();
        }


    }
}

