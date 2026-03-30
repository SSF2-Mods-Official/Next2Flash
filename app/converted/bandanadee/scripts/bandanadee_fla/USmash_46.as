package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class USmash_46 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;
        public var xframe:String;

        public function USmash_46()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 43, this.frame44, 44, this.frame45, 45, this.frame46, 47, this.frame48, 49, this.frame50, 51, this.frame52, 53, this.frame54, 69, this.frame70);
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(5),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            this.xframe = null;
            if (parent && SSF2API.isReady() && this.self && (this.self.getCurrentKirbyPower() != null))
            {
                this.self.stancePlayFrame("haspower");
            };
        }

        internal function frame4():*
        {
            if (this.self.getCurrentKirbyPower() != null)
            {
                this.self.stancePlayFrame("chargingpower");
            };
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame44():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame45():*
        {
            if (this.self.getCurrentKirbyPower() != null)
            {
                this.self.stancePlayFrame("powerattack");
            };
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
        }

        internal function frame46():*
        {
            this.self.playAttackSound(1);
            this.self.playAttackSound(2);
            this.self.playVoiceSound(1);
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame48():*
        {
            this.self.refreshAttackID();
        }

        internal function frame50():*
        {
            this.self.refreshAttackID();
        }

        internal function frame52():*
        {
            this.self.refreshAttackID();
        }

        internal function frame54():*
        {
            this.self.refreshAttackID();
            this.self.updateAttackStats({"refreshRate":999});
            this.self.updateAttackBoxStats(1, {
                "damage":8,
                "hitStun":3,
                "kbConstant":130,
                "direction":84,
                "power":40,
                "effectSound":"brawl_zap_l"
            });
            this.self.playAttackSound(3);
            this.self.attachEffect("global_dust_heavy");
            SSF2API.getCamera().shake(3);
        }

        internal function frame70():*
        {
            this.self.endAttack();
        }


    }
}

