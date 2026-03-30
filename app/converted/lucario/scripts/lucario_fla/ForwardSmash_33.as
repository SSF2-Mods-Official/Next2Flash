package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class ForwardSmash_33 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;
        public var xframe:String;

        public function ForwardSmash_33()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 42, this.frame43, 43, this.frame44, 45, this.frame46, 48, this.frame49, 50, this.frame51, 65, this.frame66, 68, this.frame69);
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
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraDamage([1]);
                this.self.updateAttackBoxStats(1, {"kbConstant":(105 - (this.self.auraPercentage * 10))});
                this.self.updateAuraPaws();
            };
        }

        internal function frame3():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame43():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame44():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
            this.self.playVoiceSound(1);
        }

        internal function frame46():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame49():*
        {
            this.self.addEffectToList(this.self.attachEffect("trail_lucario_fsmash", {
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame51():*
        {
            this.self.playAttackSound(1);
            SSF2API.getCamera().shake(5);
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame66():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame69():*
        {
            this.self.endAttack();
        }


    }
}

